# Pacote de adaptadores de scraping.
from . import net_empregos, itjobs

AVAILABLE_SCRAPERS = {
      "net-empregos": net_empregos,
      "itjobs": itjobs,
}
